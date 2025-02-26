<?php

namespace App\Filament\Resources\ProductResource\RelationManagers;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Tables;
use Filament\Tables\Columns\CheckboxColumn;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class ChildrenRelationManager extends RelationManager
{
    protected static string $relationship = 'children';
        // Atributo para mostrar como título en el listado de hijos (opcional)
    protected static ?string $recordTitleAttribute = 'menuitemtext';
    protected static ?string $title = 'Productos Hijos';

    public static function canViewForRecord(Model $ownerRecord, string $pageClass): bool
    {
        // Solo se muestra si el producto es padre (su campo menuitempopupheaderid es nulo)
        return is_null($ownerRecord->menuitempopupheaderid);
    }

    /**
     * Forzamos que el Relation Manager solo se renderice si canViewForRecord() devuelve true.
     */
    protected function shouldRender(): bool
    {
        return static::canViewForRecord($this->ownerRecord, $this->pageClass);
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('Subproductos')
                    ->required()
                    ->maxLength(255),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('Subproductos')
            ->columns([
                TextColumn::make('menuitemtext')
                ->label('Nombre Producto Hijo'),
                CheckboxColumn::make('menuiteminactive')->label('Inactivo')
                ->disabled(),
            ])
            ->filters([
                //
            ])
            ->headerActions([
                // Tables\Actions\CreateAction::make(),
            ])
            ->actions([
                // Tables\Actions\EditAction::make(),
                // Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     Tables\Actions\DeleteBulkAction::make(),
                // ]),
            ]);
    }

}
